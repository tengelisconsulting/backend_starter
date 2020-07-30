local auth = require("lua/auth")
local ez = require("lua/ez")
local log = require("lua/log")
local req_util = require("lua/req_util")
local respond = require("lua/respond")

local function handle(param_names)
   local ez_url = ngx.var.uri
   local user_id = ngx.var.user_id
   if user_id == "" or not user_id then
      user_id = auth.authenticate_req()
      if not user_id then
         return
      end
   end
   log.info("have user id %s", user_id)
   local params = req_util.get_req_params_table(param_names)
   params["user_id"] = user_id
   local res, err = ez.r("HTTP_MAP", ez_url, params)
   if err then
      respond.die(err.code, err.msg)
      return
   end
   respond.ok(res)
end

return handle
