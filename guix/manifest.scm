;; GNU Guix manifest for Agent Zero
;; This file defines the complete dependency environment for Agent Zero

(use-modules (gnu)
             (gnu packages)
             (gnu packages python)
             (gnu packages python-xyz)
             (gnu packages python-web)
             (gnu packages python-science)
             (gnu packages machine-learning)
             (gnu packages node)
             (gnu packages web)
             (gnu packages version-control)
             (gnu packages audio)
             (gnu packages ssh)
             (gnu packages admin)
             (gnu packages certs)
             (gnu packages curl)
             (gnu packages wget)
             (gnu packages base))

(packages->manifest
 (list
  ;; Core system packages
  python
  python-pip
  node
  git
  ffmpeg
  openssh
  sudo
  curl
  wget
  nss-certs
  
  ;; Python packages for web framework
  python-flask
  python-beautifulsoup4
  python-docker
  python-faiss
  python-gitpython
  python-lxml
  python-markdown
  python-paramiko
  python-pypdf2
  python-pytz
  python-tiktoken
  python-requests
  python-dotenv
  
  ;; Additional tools
  supervisor
  cron))