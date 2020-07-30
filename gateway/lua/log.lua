-- public
local function log(level, template, ...)
   local s = string.format(template, ...)
   ngx.log(level, s)
end


local function info(s, ...)
   log(ngx.INFO, s, ...)
end

local function err(s, ...)
   log(ngx.ERR, s, ...)
end

local function dbg(s, ...)
   log(ngx.DEBUG, s, ...)
end

local function table_print (tt, indent, done)
   done = done or {}
   indent = indent or 0
   if type(tt) == "table" then
      local sb = {}
      for key, value in pairs (tt) do
         table.insert(sb, string.rep (" ", indent)) -- indent it
         if type (value) == "table" and not done [value] then
            done [value] = true
            table.insert(sb, key .. " = {\n");
            table.insert(sb, table_print (value, indent + 2, done))
            table.insert(sb, string.rep (" ", indent)) -- indent it
            table.insert(sb, "}\n");
         elseif "number" == type(key) then
            table.insert(sb, string.format("\"%s\"\n", tostring(value)))
         else
            table.insert(sb, string.format(
                            "%s = \"%s\"\n", tostring (key), tostring(value)))
         end
      end
      return table.concat(sb)
   else
      return tt .. "\n"
   end
end

local M = {}
M.info = info
M.err = err
M.dbg = dbg
M.table_print = table_print
return M
