from kubernetes import client, config
from kubernetes.client.rest import ApiException

import yaml

class KubeService:
    def __init__(self):
        self.contexts = []
        self.active_context = None
        self.active_namespace = "default"
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
            self.active_namespace = "default" # Reset namespace on context switch
            return True
        except Exception as e:
            print(f"Error setting context {context_name}: {e}")
            return False

    def create_namespace(self, name):
        """Creates a new namespace."""
        try:
            v1 = client.CoreV1Api()
            namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
            v1.create_namespace(body=namespace)
            return True
        except ApiException as e:
            print(f"Error creating namespace: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error creating namespace: {e}")
            return False

    def delete_namespace(self, name):
        """Deletes a namespace."""
        try:
            v1 = client.CoreV1Api()
            v1.delete_namespace(name=name)
            return True
        except ApiException as e:
            print(f"Error deleting namespace: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error deleting namespace: {e}")
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

    def set_namespace(self, namespace):
        """Sets the active namespace."""
        self.active_namespace = namespace

    def list_deployments(self, namespace=None):
        """Returns a list of deployment names in the specified namespace."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            deployments = apps_v1.list_namespaced_deployment(target_ns)
            return [d.metadata.name for d in deployments.items]
        except ApiException as e:
            print(f"Error listing deployments: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing deployments: {e}")
            return []

    def list_cronjobs(self, namespace=None):
        """Returns a list of cronjob names in the specified namespace."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            batch_v1 = client.BatchV1Api()
            cronjobs = batch_v1.list_namespaced_cron_job(target_ns)
            return [c.metadata.name for c in cronjobs.items]
        except ApiException as e:
            print(f"Error listing cronjobs: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing cronjobs: {e}")
            return []

    def get_deployment(self, name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            return apps_v1.read_namespaced_deployment(name, target_ns)
        except ApiException as e:
            print(f"Error getting deployment: {e}")
            return None

    def get_cronjob(self, name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            batch_v1 = client.BatchV1Api()
            return batch_v1.read_namespaced_cron_job(name, target_ns)
        except ApiException as e:
            print(f"Error getting cronjob: {e}")
            return None

    def list_pods(self, label_selector, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            v1 = client.CoreV1Api()
            pods = v1.list_namespaced_pod(target_ns, label_selector=label_selector)
            return pods.items
        except ApiException as e:
            print(f"Error listing pods: {e}")
            return []

    def get_pod_logs(self, pod_name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            v1 = client.CoreV1Api()
            return v1.read_namespaced_pod_log(pod_name, target_ns)
        except ApiException as e:
            print(f"Error getting pod logs: {e}")
            return f"Error: {e}"

    def get_resource_yaml(self, resource_obj):
        try:
            api_client = client.ApiClient()
            return yaml.dump(api_client.sanitize_for_serialization(resource_obj))
        except Exception as e:
            return f"Error serializing to YAML: {e}"

# Singleton instance
kube_service = KubeService()
