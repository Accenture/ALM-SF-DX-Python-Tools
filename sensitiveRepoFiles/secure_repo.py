import os
import subprocess
import argparse
import time
import logging
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)

def call_subprocess(command):
    try:
        output = subprocess.check_output(command).decode('utf-8')
        return output.split('\n')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar el comando {command}: {str(e)}")
        return []

def get_main_branches():
    main_branches           = ['origin/release', 'origin/master', 'origin/main', 'origin/develop']
    existing_branches       = subprocess.check_output(['git', 'branch', '-r']).decode('utf-8').split('\n')
    existing_branches       = [branch.strip() for branch in existing_branches]
    existing_main_branches  = [branch for branch in main_branches if branch in existing_branches]
    return existing_main_branches

def get_all_branches():
    branches = subprocess.check_output(['git', 'for-each-ref', '--format=%(refname:short)', 'refs/heads', 'refs/remotes']).decode('utf-8').split('\n')
    cleaned_branches = [branch for branch in branches if branch]
    return cleaned_branches

def search_sensitive_files(repo_path, main_only):
    sensitive_extensions = ['.key', '.crt', '.pem', '.p12', '.pfx', '.cer', '.der', '.jks', '.keystore', '.ovpn', '.aes', '.asc', '.ovpn', '.p7b', '.p7c', '.p8', '.pkcs12', '.pse', '.sst', '.stl', '.p12', '.pfx', '.p7b', '.spc', '.p7r', '.p7c', '.der', '.cer', '.crt', '.pem', '.env', '.ini', '.toml', '.cfg', '.conf', '.config', '.properties', '.prop', '.props', '.cnf', '.rc', '.inf', '.info', '.plist']

    if not os.path.exists(repo_path):
        logging.error(f"La ruta al repositorio {repo_path} no existe.")
        return {}

    os.chdir(repo_path)
    branches = get_main_branches() if main_only else get_all_branches()
    results = {}

    for branch in branches:
        call_subprocess(['git', 'checkout', branch])
        # call_subprocess(['git', 'pull', 'origin', branch.split('/')[-1]])
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if any(file.endswith(ext) for ext in sensitive_extensions):
                    full_path = os.path.join(root, file)
                    if os.path.exists(full_path):
                        commits = call_subprocess(['git', 'log', '--pretty=format:%H', '--', full_path])
                        relative_path = os.path.relpath(full_path, repo_path)
                        if relative_path not in results:
                            results[relative_path] = {branch: commits}
                        else:
                            results[relative_path][branch] = commits

    return results

def main():
    parser = argparse.ArgumentParser(description='Busca archivos sensibles en un repositorio git.')
    parser.add_argument('repo_path', help='La ruta al repositorio git.')
    parser.add_argument('--main_only', action='store_true', help='Solo busca en las ramas principales (release, master, main, develop).')
    args = parser.parse_args()

    script_dir      = os.path.dirname(os.path.abspath(__file__))
    template_dir    = script_dir
    template_name   = 'template.html'
    template_path   = os.path.join(template_dir, template_name)

    if not os.path.exists(template_path):
        logging.error(f"La plantilla {template_path} no existe.")
        return

    results = search_sensitive_files(args.repo_path, args.main_only)

    if results:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        html = template.render(results=results)

        with open('results.html', 'w') as f:
            f.write(html)

        logging.info(f"Los resultados se han escrito en {args.repo_path}/results.html")
    else:
        logging.info("No se encontraron resultados.")

if __name__ == '__main__':
    main()
