from kubernetes import client, config
from kubernetes.client.rest import ApiException

import yaml
import json
import os

class KubeService:
    def __init__(self):
        self.contexts = []
        self.active_context = None
        self.active_namespace = "default"
        self._custom_contexts_file = "storage/custom_contexts.json"
        self._load_config()

    def _load_config(self):
        self.contexts = []
        
        # 1. Load system kube config
        try:
            config.load_kube_config()
            system_contexts, active_context = config.list_kube_config_contexts()
            self.contexts.extend(system_contexts)
            self.active_context = active_context
        except Exception as e:
            print(f"Error loading system kube config: {e}")
            
        # 2. Load custom contexts
        self._load_custom_contexts()

    def _load_custom_contexts(self):
        if not os.path.exists(self._custom_contexts_file):
            return

        try:
            with open(self._custom_contexts_file, 'r') as f:
                custom_contexts = json.load(f)
                
            for ctx in custom_contexts:
                # Format to match kubernetes client structure
                formatted_ctx = {
                    'name': ctx['name'],
                    'context': {
                        'cluster': ctx['name'],
                        'user': ctx['name']
                    },
                    'is_custom': True,
                    'config': ctx # Store full config for later use
                }
                # Check for duplicates before adding
                if not any(c['name'] == ctx['name'] for c in self.contexts):
                    self.contexts.append(formatted_ctx)
                    
        except Exception as e:
            print(f"Error loading custom contexts: {e}")

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
            # Find the context object
            target_ctx = next((ctx for ctx in self.contexts if ctx['name'] == context_name), None)
            
            if not target_ctx:
                return False

            if target_ctx.get('is_custom'):
                # Handle custom context loading
                ctx_config = target_ctx['config']
                configuration = client.Configuration()
                configuration.host = ctx_config['server']
                configuration.verify_ssl = not ctx_config.get('insecure', False)
                configuration.api_key = {"authorization": "Bearer " + ctx_config['token']}
                
                # Create a client from the configuration
                api_client = client.ApiClient(configuration)
                client.Configuration.set_default(configuration)
                
                self.active_context = target_ctx
            else:
                # Handle standard kubeconfig context
                config.load_kube_config(context=context_name)
                self.active_context = target_ctx
            
            self.active_namespace = "default" # Reset namespace on context switch
            return True
        except Exception as e:
            print(f"Error setting context {context_name}: {e}")
            return False

    def add_custom_context(self, name, server, token, insecure=False):
        """Adds a new custom context."""
        new_context = {
            "name": name,
            "server": server,
            "token": token,
            "insecure": insecure
        }
        
        try:
            custom_contexts = []
            if os.path.exists(self._custom_contexts_file):
                with open(self._custom_contexts_file, 'r') as f:
                    custom_contexts = json.load(f)
            
            # Check if name already exists
            if any(ctx['name'] == name for ctx in custom_contexts):
               return False, "Context name already exists"

            custom_contexts.append(new_context)
            
            with open(self._custom_contexts_file, 'w') as f:
                json.dump(custom_contexts, f, indent=4)
            
            # Reload configs to update the list
            self._load_config()
            return True, "Context added successfully"
        except Exception as e:
            return False, f"Error saving context: {e}"

    def delete_custom_context(self, name):
        """Deletes a custom context."""
        try:
            if not os.path.exists(self._custom_contexts_file):
                return False, "Storage file not found"

            with open(self._custom_contexts_file, 'r') as f:
                custom_contexts = json.load(f)
            
            initial_len = len(custom_contexts)
            custom_contexts = [ctx for ctx in custom_contexts if ctx['name'] != name]
            
            if len(custom_contexts) == initial_len:
                return False, "Context not found"

            with open(self._custom_contexts_file, 'w') as f:
                json.dump(custom_contexts, f, indent=4)

            # Reload configs
            self._load_config()
            return True, "Context deleted successfully"
        except Exception as e:
            return False, f"Error deleting context: {e}"

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

    def scale_deployment(self, name, replicas, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            body = {'spec': {'replicas': int(replicas)}}
            apps_v1.patch_namespaced_deployment_scale(name, target_ns, body)
            return True, "Scaled successfully"
        except ApiException as e:
            return False, f"Error scaling: {e}"

    def restart_deployment(self, name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            body = {
                'spec': {
                    'template': {
                        'metadata': {
                            'annotations': {
                                'kubectl.kubernetes.io/restartedAt': now.isoformat()
                            }
                        }
                    }
                }
            }
            apps_v1.patch_namespaced_deployment(name, target_ns, body)
            return True, "Restart triggered"
        except ApiException as e:
            return False, f"Error restarting: {e}"

    def delete_deployment(self, name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            apps_v1.delete_namespaced_deployment(name, target_ns)
            return True, "Deleted successfully"
        except ApiException as e:
            return False, f"Error deleting: {e}"

    def create_deployment(self, name, image, replicas, selector_label, env_vars, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            
            # Parse selector label "key=value"
            if "=" in selector_label:
                key, value = selector_label.split("=", 1)
                labels = {key.strip(): value.strip()}
            else:
                labels = {"app": selector_label.strip()}

            # Parse env vars dict to V1EnvVar list
            k8s_env_vars = []
            for k, v in env_vars.items():
                k8s_env_vars.append(client.V1EnvVar(name=k, value=v))

            container = client.V1Container(
                name=name,
                image=image,
                env=k8s_env_vars,
                ports=[client.V1ContainerPort(container_port=80)] # Default port, can be improved
            )

            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(containers=[container])
            )

            spec = client.V1DeploymentSpec(
                replicas=int(replicas),
                selector=client.V1LabelSelector(match_labels=labels),
                template=template
            )

            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=name, labels=labels),
                spec=spec
            )

            apps_v1.create_namespaced_deployment(namespace=target_ns, body=deployment)
            return True, "Deployment created successfully"
        except ApiException as e:
            return False, f"Error creating deployment: {e}"

    def update_deployment(self, name, image, env_vars, namespace=None):
        """Updates image and environment variables of the first container."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            
            # Fetch existing to get current spec
            deployment = apps_v1.read_namespaced_deployment(name, target_ns)
            
            # Update container 0
            if deployment.spec.template.spec.containers:
                container = deployment.spec.template.spec.containers[0]
                container.image = image
                
                # Transform env vars
                k8s_env_vars = []
                for k, v in env_vars.items():
                    k8s_env_vars.append(client.V1EnvVar(name=k, value=v))
                
                container.env = k8s_env_vars
                
                # Patch
                apps_v1.patch_namespaced_deployment(name, target_ns, deployment)
                return True, "Deployment updated successfully"
            else:
                 return False, "No containers found in deployment"
                 
        except ApiException as e:
            return False, f"Error updating deployment: {e}"

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

    def list_statefulsets(self, namespace=None):
        """Returns a list of statefulset objects in the specified namespace."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            statefulsets = apps_v1.list_namespaced_stateful_set(target_ns)
            return statefulsets.items
        except ApiException as e:
            print(f"Error listing statefulsets: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing statefulsets: {e}")
            return []

    def get_deployment(self, name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            return apps_v1.read_namespaced_deployment(name, target_ns)
        except ApiException as e:
            print(f"Error getting deployment: {e}")
            return None

    def get_statefulset(self, name, namespace=None):
        target_ns = namespace if namespace else self.active_namespace
        try:
            apps_v1 = client.AppsV1Api()
            return apps_v1.read_namespaced_stateful_set(name, target_ns)
        except ApiException as e:
            print(f"Error getting statefulset: {e}")
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
                
            if target_ns == "all":
                pods = v1.list_pod_for_all_namespaces(label_selector=selector_str)
            else:
                pods = v1.list_namespaced_pod(target_ns, label_selector=selector_str)
            return pods.items
        except ApiException as e:
            print(f"Error listing pods: {e}")
            return []

    def get_pod_metrics(self, namespace=None):
        """Returns a dict of pod metrics keyed by pod name."""
        try:
            custom_api = client.CustomObjectsApi()
            if namespace and namespace != "all":
                metrics = custom_api.list_namespaced_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    namespace=namespace,
                    plural="pods"
                )
            else:
                 metrics = custom_api.list_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
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

    def get_node_metrics(self):
        """Returns a dict of node metrics keyed by node name."""
        try:
            custom_api = client.CustomObjectsApi()
            metrics = custom_api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes"
            )
            
            metrics_map = {}
            for item in metrics.get('items', []):
                node_name = item['metadata']['name']
                metrics_map[node_name] = item
            
            return metrics_map
        except ApiException as e:
            print(f"Error listing node metrics: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error listing node metrics: {e}")
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

    def list_nodes(self):
        """Returns a list of all nodes in the cluster."""
        try:
            v1 = client.CoreV1Api()
            nodes = v1.list_node()
            return nodes.items
        except ApiException as e:
            print(f"Error listing nodes: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing nodes: {e}")
            return []

    def list_events(self, namespace=None):
        """Returns a list of events in the specified namespace."""
        target_ns = namespace if namespace else self.active_namespace
        try:
            v1 = client.CoreV1Api()
            events = v1.list_namespaced_event(target_ns)
            # Sort by last timestamp descending
            sorted_events = sorted(
                events.items, 
                key=lambda x: x.last_timestamp or x.event_time or x.metadata.creation_timestamp, 
                reverse=True
            )
            return sorted_events
        except ApiException as e:
            print(f"Error listing events: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing events: {e}")
            return []

    def check_connection(self):
        """Checks if the connection to the cluster is valid."""
        try:
            v1 = client.CoreV1Api()
            v1.list_node(limit=1)
            return True
        except Exception as e:
            print(f"Connection check failed: {e}")
            return False

# Singleton instance
kube_service = KubeService()
