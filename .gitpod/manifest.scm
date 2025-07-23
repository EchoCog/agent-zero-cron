;; GNU Guix manifest for Agent Zero Gitpod deployment
;; Optimized for gitpod/workspace-python-3.10 environment

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
             (gnu packages base)
             (gnu packages package-management))

(packages->manifest
 (list
  ;; Core system packages (minimal set for Gitpod)
  git
  curl
  wget
  nss-certs
  
  ;; Python packages essential for Agent Zero
  python-flask
  python-beautifulsoup4
  python-requests
  python-lxml
  python-markdown
  python-pytz
  python-dotenv
  
  ;; Additional tools that work well in Gitpod
  ffmpeg
  openssh))

;; Note: This is a minimal manifest optimized for Gitpod
;; The gitpod/workspace-python-3.10 base image already provides:
;; - Python 3.10 and pip
;; - Node.js
;; - Many common development tools
;; 
;; We only add packages that are:
;; 1. Not available in the base image
;; 2. Specifically required for Agent Zero
;; 3. Benefit from Guix's reproducible builds