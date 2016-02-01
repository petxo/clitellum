from clitellum.endpoints.channels import factories
from config import Config

cfg = Config("myoutbound.cfg")
pb = factories.CreateOutBoundChannelFromConfig(cfg)





