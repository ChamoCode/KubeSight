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
        """Returns a list of deployment objects in the specified namespace."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            deployments = apps_v1.list_namespaced_deployment(target_ns)
            return deployments.items
        except ApiException as e:
            print(f"Error listing deployments: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing deployments: {e}")
            return []

    def list_cronjobs(self, namespace=None):
        """Returns a list of cronjob objects in the specified namespace."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            batch_v1 = client.BatchV1Api()
            cronjobs = batch_v1.list_namespaced_cron_job(target_ns)
            return cronjobs.items
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
            # Convert dict selector to string if needed
            if isinstance(label_selector, dict):
                selector_str = ",".join([f"{k}={v}" for k, v in label_selector.items()])
            else:
                selector_str = label_selector
                
            pods = v1.list_namespaced_pod(target_ns, label_selector=selector_str)
            return pods.items
        except ApiException as e:
            print(f"Error listing pods: {e}")
            return []

    def get_pod_metrics(self, namespace=None):
        """Returns a dict of pod metrics keyed by pod name."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            custom_api = client.CustomObjectsApi()
            metrics = custom_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=target_ns,
                plural="pods"
            )
            
            metrics_map = {}
            for item in metrics.get('items', []):
                pod_name = item['metadata']['name']
                containers = item.get('containers', [])
                
                # Aggregate container metrics
                total_cpu = 0
                total_mem = 0
                
                for c in containers:
                    cpu_str = c['usage']['cpu']
                    mem_str = c['usage']['memory']
                    
                    # Simple parsing (approximate)
                    # CPU: 100n, 10u, 1m -> convert to nanocores or millicores? 
                    # Let's keep strings for display or do simple conversion if needed.
                    # For now, just storing the raw first container or summing if we parse.
                    # To keep it simple for display, let's just store the raw values of the first container
                    # or try to sum them up if we can parse.
                    
                    # Let's just store the raw list of container metrics for the view to handle
                    pass

                metrics_map[pod_name] = item
            
            return metrics_map
        except ApiException as e:
            print(f"Error listing pod metrics: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error listing pod metrics: {e}")
            return {}

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
