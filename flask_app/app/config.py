class Config:
    DEBUG = False
    TESTING = False
    BUCKET_NAME = "ai-podcast-cards"
    SUM_PREFIX = "summaries/"
    PODCASTS = ["Dwarkesh Podcast", "Latent Space"]


class ProdConfig(Config):
    pass


class TestConfig(Config):
    DEBUG = True
    TESTING = True
