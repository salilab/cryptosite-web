import saliweb.build

vars = Variables('config.py')
env = saliweb.build.Environment(vars, ['conf/live.conf'], service_module='cryptosite')
Help(vars.GenerateHelpText(env))

env.InstallAdminTools()

Export('env')
SConscript('backend/cryptosite/SConscript')
SConscript('frontend/cryptosite/SConscript')
SConscript('test/SConscript')
