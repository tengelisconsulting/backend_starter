local cjson = require "cjson"

local ez_client = require("ez_client")

local env = require("lua/env")
local log = require("lua/log")

-- private
log.info("setting requester")
local requester = ez_client.new_requester(
   env.EZ_INPUT_HOST, env.EZ_INPUT_PORT
)

-- public

local M = {}
function M.r(service, url, body, opts)
   local body = cjson.encode(body)
   local frames = {service, url, body}
   local res, err = requester(frames, opts)
   if err then
      log.err(tostring(err))
      return nil, {code = 500, msg = "server error"}
   end
   local ok, res_body = unpack(res)
   res_body = cjson.decode(res_body)
   if res_body == "" or res_body == ngx.null then
      res_body = nil
   end
   if ok == "ERR" then
      return nil, res_body
   end
   return res_body, nil
end

function M.r_json(service, url, body, opts)
   local res, err = M.r(service, url, body, opts)
   if err or not res then
      return res, err
   end
   local res, decode_err = cjson.decode(res)
   if decode_err then
      return nil, {code = 500, msg = "server error"}
   end
   return res, nil
end

return M
