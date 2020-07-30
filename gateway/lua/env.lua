local os = require "os"

local M = {}
M.EZ_INPUT_HOST = os.getenv("EZ_INPUT_HOST")
M.EZ_INPUT_PORT = tonumber(os.getenv("EZ_INPUT_PORT"))
return M
