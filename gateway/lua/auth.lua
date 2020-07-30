local cjson = require "cjson"
local ck = require "resty.cookie"

local ez = require "lua/ez"
local log = require "lua/log"
local req_util = require "lua/req_util"
local respond = require "lua/respond"


local REFRESH_TOKEN_NAME = "ONWARD_REFRESH_TOKEN"

local REFRESH_TOKEN = "REFRESH"
local SESSION_TOKEN = "SESSION"


-- private
local function adjust_authed_req(user_id)
   ngx.var.user_id = user_id
   ngx.req.set_header("user-id", user_id)
end



local M = {}
M.REFRESH_TOKEN_NAME = "ONWARD_REFRESH_TOKEN"
M.REFRESH_TOKEN = "REFRESH"
M.SESSION_TOKEN = "SESSION"

function M.new_session(user_id)
   local function get_token(token_type)
      local res, err = ez.r("AUTHENTICATE", "/token/issue", {
                               user_id = user_id,
                               token_type = token_type})
      if err then
         respond.die(401, "token err")
         return nil
      end
      return res.token
   end
   local refresh_token = get_token(REFRESH_TOKEN)
   if not refresh_token then
      return
   end
   local session_token = get_token(SESSION_TOKEN)
   if not session_token then
      return
   end
   local cookie = ck:new()
   local ok, err = cookie:set({
         key = REFRESH_TOKEN_NAME,
         value = refresh_token,
         path = "/",
         http_only = true,
   })
   if err then
      respond.die(401, err)
      return
   end
   respond.ok({session_token = session_token})
end

function M.authenticate_req()
   local auth_header = ngx.var.http_authorization
   if not auth_header then
      respond.die(401, "provide 'authorization' header")
      return
   end
   local claims, err = ez.r("AUTHENTICATE", "/creds/parse/bearer", {
                               creds = auth_header,
                               token_type = SESSION_TOKEN})
   if err then
      respond.die(401, err)
      return
   end
   adjust_authed_req(claims.user_id)
   return claims.user_id
end

function M.authorize_req()
   local auth_data = {
      user_id = ngx.var.user_id,
      method = ngx.req.get_method(),
      url = ngx.var.request_uri
   }
   local res, err = ez.r("AUTHORIZE", "/authorize/url", auth_data)
   if err then
      respond.die(403, err)
      return false
   end
   if not res then
      respond.die(403, "unauthorized")
      return false
   end
   return true
end

function M.send_verify_email(user_id, user_email)
   local verify_secret, err = ez.r("CRYPTO", "/random/int", {n_bytes = 8})
   if err then
      return nil, err
   end
   local verify_secret_hash, err = ez.r("CRYPTO", "/hash/standard", {
                                           body = verify_secret})
   if err then
      return nil, err
   end
   local adhoc_data = cjson.encode({verify_secret_hash = verify_secret_hash})
   local update_res, err = ez.r_json("DB", "/user_update_adhoc", {
                                        p_user_id = user_id,
                                        p_adhoc = adhoc_data})
   if err then
      return nil, err
   end
   local mail_template, err = ez.r("MAIL_TEMPLATE", "/get/ACCOUNT_VERIFY", {
                                      user_email = user_email,
                                      verify_secret = verify_secret})
   if err then
      return nil, err
   end
   local mail_res, err = ez.r("USER_MAIL", "/start_thread", {
                                 user_id = user_id,
                                 msg_type = "ACCOUNT_VERIFY",
                                 subject = mail_template.subject,
                                 body = mail_template.body,
                                 adhoc = {}})
   return mail_res, nil
end

function M.attempt_verify_account(user_id, verify_secret)
   local adhoc_data, err = ez.r_json("DB", "/user_get_adhoc",
                                    {p_user_id = user_id})
   if err then
      return nil, err
   end
   local exp_hash = adhoc_data.verify_secret_hash
   local match, err = ez.r("CRYPTO", "/verify-hash/standard", {
                              body = verify_secret,
                              provided_hash = exp_hash})
   if err then
      return nil, err
   end
   local res, err = ez.r_json("DB", "/user_update_adhoc", {
                                 p_user_id = user_id,
                                 p_adhoc = cjson.encode({
                                       verified = true}
   )})
   return res, err
end

return M
