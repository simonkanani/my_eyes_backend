from storages.backends.azure_storage import AzureStorage


class PublicAzureStorage(AzureStorage):
    account_name = '00672020team18diag'
    accountkey = 'gHeUIh1I6yH3aTMmLCVBzdMwXFvSZUb6AU2efk3Lvau8rwJzrNpOpdGGJcDo7OWckE7HJRkpTlHcGIY5/IzYDg=='
    azure_container = 'my-eyes-container'
    expiration_secs = None
