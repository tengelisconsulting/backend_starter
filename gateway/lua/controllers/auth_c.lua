local ck = require "resty.cookie"
local cjson = require("cjson")

local auth = require "lua/auth"
local ez = require "lua/ez"
local log = require "lua/log"
local req_util = require "lua/req_util"
local respond = require "lua/respond"


local M = {}
function M.authenticate_provider()
   local token, provider_type = req_util.get_req_params({"token",
                                                         "provider_type"})
   if not token then
      respond.die(401, "provide 'token'")
      return
   end
   if not provider_type then
      respond.die(401, "provide 'provider_type'")
      return
   end
   local user_id, err = ez.r("AUTH_PROVIDER",
                                "/authenticate/" .. provider_type,
                                {token = token})
   if err then
      respond.die(401, "failed to parse provider token")
      return
   end
   auth.new_session(user_id)
end

function M.authenticate_username_password()
   local email, password = req_util.get_req_params({"email", "password"})
   local user, err = ez.r_json("DB", "/get_user_slim", {
                                   p_email = email
   })
   if err then
      respond.die(500, "failed to fetch user")
   end
   if not user then
      respond.die(401, string.format("no such user %s", email))
      return
   end
   if not user.verified then
      respond.die(401, "user is not verified")
      return
   end
   local pw_match, err = ez.r("CRYPTO", "/verify-hash/standard", {
                                 body = password,
                                 provided_hash = user.pw_hash})
   if err or not pw_match then
      respond.die(401, "user login failed")
      return
   end
   auth.new_session(user.user_id)
end

function M.end_session()
   local cookie = ck:new()
   local ok, err = cookie:set({
         key = auth.REFRESH_TOKEN_NAME,
         value = "",
         path = "/",
         http_only = true,
   })
   respond.ok("OK")
end


function M.renew_session()
   local cookie = ck:new()
   local refresh_token, err = cookie:get("ONWARD_REFRESH_TOKEN")
   if not refresh_token then
      respond.die(401, "no refresh token")
   end
   local claims, err = ez.r("AUTHENTICATE", "/token/parse",
                            {token = refresh_token,
                             token_type = auth.REFRESH_TOKEN})
   if not claims then
      respond.die(401, "bad refresh token")
   end
   auth.new_session(claims.user_id)
end

function M.new_user()
   local email, password, timezone = req_util.get_req_params(
      {"email", "password", "timezone"})
   local user, err = ez.r_json("DB", "/get_user_slim", {
                                   p_email = email
   })
   if user then
      log.err("loaded existing user: %s", user.user_id)
      respond.die(401, "user exists")
      return
   end
   local pw_hash, err = ez.r("CRYPTO", "/hash/standard", {
                                body = password})
   if err then
      log.err(log.table_print(err))
      respond.die(500, "failed to hash pw")
      return
   end
   local user_res, err = ez.r_json("DB", "/new_user_pw", {
                            p_email = email,
                            p_pw_hash = pw_hash,
                            p_timezone = timezone})
   local user_id = user_res.user_id
   if err then
      log.err(log.table_print(err))
      respond.die(500, "create user failed")
      return
   end
   local res, err = auth.send_verify_email(user_id, email)
   if err then
      log.err("failed to send verify email: %s", err)
   end
   respond.ok({user_id = user_id})
end


function M.new_provider_user()
   local token, provider_type = req_util.get_req_params({
         "token", "provider_type", "timezone"})
   local user_id, err = ez.r("AUTH_PROVIDER","/init/" .. provider_type,
                             {token = token, timezone = timezone})
   if err then
      log.err(log.table_print(err))
      respond.die(500, "create user failed")
      return
   end
   respond.ok({user_id = user_id})
end

function M.verify_account()
   local user_id, verify_secret = req_util.get_req_params({
         "user_id", "verify_secret"})
   local success, err = auth.attempt_verify_account(user_id, verify_secret)
   if err or not success then
      log.err(log.table_print(err))
      respond.die(401, "verify failed")
      return
   end
   respond.ok({verified = true})
end

return M
