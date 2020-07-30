local auth = require("lua/auth")
local ez = require("lua/ez")
local log = require("lua/log")
local req_util = require("lua/req_util")
local respond = require("lua/respond")


local M = {}
function M.ez_handle(param_names)
   local ez_url = ngx.var.uri;
   log.info("req for %s", ez_url)
   local user_id = auth.authenticate_req()
   if not user_id then
      return
   end
   local params = req_util.get_req_params_table(param_names)
   params["user_id"] = user_id
   local permitted, err = ez.r("AUTHORIZE", "/authorize/ez_url", {
                                  user_id = user_id,
                                  ez_url = ez_url,
                                  args = params})
   if err or not permitted then
      respond.die(403, "Unauthorized")
      return
   end
   local res, err = ez.r("HTTP_MAP", ez_url, params)
   if err then
      respond.die(err.code, err.msg)
      return
   end
   respond.ok(res)
end

function M.access_by_ez(route, extra_args)
   local ez_params = {user_id = ngx.var.user_id}
   if extra_args then
      local req_params = {req_util.get_req_params(extra_args)}
      for i, v in ipairs(req_params) do
         ez_params[extra_args[i]] = v
      end
   end
   local res, err = ez.r("AUTHORIZE", route, ez_params)
   if err or not res then
      log.err("unauthorized: %s", err)
      respond.die(403, "Unauthorized")
      return
   end
end

function M.access_handle(endpoint_mod, endpoint_fn, param_list)
   local mod = require("lua/endpoints/access/" .. endpoint_mod)
   local fn = mod[endpoint_fn]
   local res, err
   if param_list then
      res, err = fn(req_util.get_req_params(param_list))
   else
      res, err = fn()
   end
   if err then
      respond.die(err.code, err.msg)
      return
   end
   if not res then
      respond.die(403, "Unauthorized")
      return
   end
   return true
end

function M.content_handle(endpoint_mod, endpoint_fn, param_list)
   local mod = require("lua/endpoints/content/" .. endpoint_mod)
   local fn = mod[endpoint_fn]
   local res, err
   if param_list then
      res, err = fn(req_util.get_req_params(param_list))
   else
      res, err = fn()
   end
   if err then
      respond.die(err.code, err.msg)
      return
   end
   respond.ok(res)
end
return M
