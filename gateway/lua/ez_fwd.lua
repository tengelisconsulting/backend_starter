local auth = require("lua/auth")
local ez = require("lua/ez")
local log = require("lua/log")
local req_util = require("lua/req_util")
local respond = require("lua/respond")

local M = {}
function M.handle_noauth()
   local ez_url = ngx.var.uri
   local params = req_util.get_body_table()
   local res, err = ez.r("HTTP_MAP", ez_url, params)
   if err then
      respond.die(err.code, err.msg)
      return
   end
   respond.ok(res)
end
return M
