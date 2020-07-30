local cjson = require "cjson"

local M = {}
function M.get_body_table()
   ngx.req.read_body()
   return cjson.decode(ngx.req.get_body_data())
end

function M.get_body_string()
   ngx.req.read_body()
   return ngx.req.get_body_data()
end

function M.get_req_params(param_names)
   ngx.req.read_body()
   local req_data = cjson.decode(ngx.req.get_body_data())
   local params = {}
   for i, param_name in ipairs(param_names) do
      params[i] = req_data[param_name]
   end
   return unpack(params)
end

function M.get_req_params_table(param_names)
   ngx.req.read_body()
   local req_data = cjson.decode(ngx.req.get_body_data())
   local params = {}
   for i, param_name in ipairs(param_names) do
      params[param_name] = req_data[param_name]
   end
   return params
end
return M
