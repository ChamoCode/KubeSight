from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubeService:
    def __init__(self):
        self.contexts = []
        self.active_context = None
        self._load_config()

    def _load_config(self):
        try:
            # Load kube config from default location (~/.kube/config)
            config.load_kube_config()
            self.contexts, self.active_context = config.list_kube_config_contexts()
        except Exception as e:
            print(f"Error loading kube config: {e}")
            self.contexts = []
            self.active_context = None

    def get_contexts(self):
        """Returns a list of context names."""
        if not self.contexts:
            return []
        return [context['name'] for context in self.contexts]

    def get_active_context_name(self):
        """Returns the name of the current active context."""
        if self.active_context:
            return self.active_context['name']
        return None

    def set_context(self, context_name):
        """Sets the active context and reloads the client."""
        try:
            config.load_kube_config(context=context_name)
            # Update internal active context reference
            for ctx in self.contexts:
                if ctx['name'] == context_name:
                    self.active_context = ctx
                    break
            return True
        except Exception as e:
            print(f"Error setting context {context_name}: {e}")
            return False

    def get_namespaces(self):
        """Returns a list of namespace names for the current context."""
        try:
            v1 = client.CoreV1Api()
            namespaces = v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except ApiException as e:
            print(f"Error listing namespaces: {e}")
            return []
        except Exception as e:
             print(f"Unexpected error listing namespaces: {e}")
             return []

    def list_deployments(self, namespace="default"):
        """Returns a list of deployment names in the specified namespace."""
        try:
            apps_v1 = client.AppsV1Api()
            deployments = apps_v1.list_namespaced_deployment(namespace)
            return [d.metadata.name for d in deployments.items]
        except ApiException as e:
            print(f"Error listing deployments: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing deployments: {e}")
            return []

    def list_cronjobs(self, namespace="default"):
        """Returns a list of cronjob names in the specified namespace."""
        try:
            batch_v1 = client.BatchV1Api()
            cronjobs = batch_v1.list_namespaced_cron_job(namespace)
            return [c.metadata.name for c in cronjobs.items]
        except ApiException as e:
            print(f"Error listing cronjobs: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing cronjobs: {e}")
            return []

# Singleton instance
kube_service = KubeService()
