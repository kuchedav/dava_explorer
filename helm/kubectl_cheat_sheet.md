# Kubectl Cheat Sheet

## Command alias
add following commands to {mac: ~/.bash_profile}

```bash
alias k="kubectl"
alias kg='kubectl get'
alias kd='kubectl describe'
alias kdel='kubectl delete'
alias ke='kubectl exec -it'
```

## debugging
### Start and enter Buybox
```
kubectl run -i --tty busybox --image=busybox --restart=Never -- sh
```

### Port forwarding
```
kubectl port-forward pods/pod_name pod_port:outside_port
```
