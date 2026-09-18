class GitHubCredentialGateway:
    def hydrateGithubGatewayCredentials(self, registry):
        token = registry.require("github.token")
        return {"Authorization": f"Bearer {token}"}
