## Начало работы (Prerequisites)

# Установка SSH
sudo apt update && sudo apt install -y openssh-server
sudo systemctl enable --now ssh

# Разрешить sudo без пароля (редактировать через sudo visudo)
# Добавить в конец файла:
olga2 ALL=(ALL) NOPASSWD:ALL

# Перед запуском автоматизации необходимо настроить доступ по SSH-ключам от управляющей машины (WSL) к целевым нодам:

# 1. Генерируем ключ на WSL:
   ```bash
   ssh-keygen -t ed25519 -C "ansible-key"
   ```
# 2. Копируем ключ на ноды:
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub user@<CURRENT_IP>
   ```

# На новых ВМ:
sudo apt update && sudo apt install -y openssh-server
sudo systemctl enable --now ssh

#Дать возможность пользователю не вводить пароль при sudo
user ALL=(ALL) NOPASSWD:ALL

#Прописать в inventory.ini конфиг для смены IP на ВМ
[app]
192.168.1.57 static_ip=192.168.1.10 interface_name=enp0s3

[infra]
192.168.1.114 static_ip=192.168.1.20 interface_name=enp0s3

[all:vars]
ansible_user=olga2
ansible_ssh_private_key_file=~/.ssh/id_ed25519
gateway=192.168.1.1
dns_server=8.8.8.8

#Запустить playbook
ansible-playbook playbook.yml -K

#Выполнить на VM команду для применения сетевого конфига
sudo netplan apply

#Сменить IP адреса на новые в inventory.ini
[app]
192.168.1.10 static_ip=192.168.1.10 interface_name=enp0s3

[infra]
192.168.1.20 static_ip=192.168.1.20 interface_name=enp0s3

#Запустить playbook повторно на новых адресах
ansible-playbook playbook.yml -K

#Добавить PAT для раннеров в Ansible Vault
# 1 Создать secrets файл
ansible-vault create ansible/vars/secrets.yml
# 2 Добавить в него PAT токен
github_access_token: "PAT_TOKEN"

# Создать шаблон j2 с переменными окружения
touch ansible/templates/runner.env.j2

# Добавить в него строки (REPO_URL=https адрес репозитория, указывать без кавычек)
RUNNER_NAME={{ inventory_hostname }}-runner
REPO_URL=
ACCESS_TOKEN={{ github_access_token }}
RUNNER_CLEANUP_SIGTERM=true
RUNNER_REPLACE_EXISTING=true
LABELS={% if 'app' in group_names %}app{% else %}infra{% endif %},self-hosted
RUNNER_LABELS={% if 'app' in group_names %}app{% else %}infra{% endif %},self-hosted

# Создать плейбук ansible deploy_runner.yml
touch ansible/deploy_runner.yml
# Добавить в него следующие строки
- name: Deploy GitHub Runner
  hosts: all
  become: true
  vars_files:
    - vars/secrets.yml
  tasks:
    - name: Install Docker SDK for Python
      apt:
        name: python3-docker
        state: present

    - name: Ensure runner directory exists
      file:
        path: /opt/github-runner
        state: directory
        mode: '0755'

    - name: Create .env file from template
      template:
        src: templates/runner.env.j2
        dest: /opt/github-runner/.env
        mode: '0600' # Секретный файл видит только владелец

    - name: Run GitHub Runner container
      shell: |
        docker rm -f github-runner || true
        docker run -d \
          --name github-runner \
          --restart always \
          --env-file /opt/github-runner/.env \
          -v /var/run/docker.sock:/var/run/docker.sock \
          # Монтируем корень в корень, чтобы пути совпали
          -v /opt/github-runner/work:/_work \ 
          myoung34/github-runner:latest

# Запустить плейбук для деплоя раннеров из директории ansible
ansible-playbook deploy_runner.yml --ask-vault-pass -K
