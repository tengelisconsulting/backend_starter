local auth = require("lua/auth")
local ez = require("lua/ez")
local log = require("lua/log")
local req_util = require("lua/req_util")
local respond = require("lua/respond")

local M = {}
function M.user_owns(obj_id_param)
   local ez_url = ngx.var.uri
   local user_id = auth.authenticate_req()
   if not user_id then
      return
   end
   local params = req_util.get_req_params_table({obj_id_param})
   params["user_id"] = user_id
   local permitted, err = ez.r("AUTHORIZE", "/policy/user-owns", {
                                  user_id = user_id,
                                  obj_id = params[obj_id_param]})
   if err or not permitted then
      respond.die(403, "Unauthorized")
      return
   end
end
function M.user_belongs_to(group_id_param)
   local ez_url = ngx.var.uri
   local user_id = auth.authenticate_req()
   if not user_id then
      return
   end
   local params = req_util.get_req_params_table({group_id_param})
   params["user_id"] = user_id
   local permitted, err = ez.r("AUTHORIZE", "/policy/user-belongs-to", {
                                  user_id = user_id,
                                  group_id = params[group_id_param]})
   if err or not permitted then
      respond.die(403, "Unauthorized")
      return
   end
end

return M
