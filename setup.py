from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(name="herotools",
      version="1.0.0",
      packages=['akamaiopen', 'akamaiopen.cloudlets', 'akamaiopen.cloudlets.matches', 'endpoints', 'cloudlets', 'sa2020', 'akau'],
      entry_points={
          'console_scripts': [
              'generate-prc-rules=endpoints.cli:generate_rules',
              'cloudlet-validate-policy=cloudlets.cli:validate_policy',
              'cloudlet-policy-update=cloudlets.cli:update_policy',
              'cloudlet-policy-activate=cloudlets.cli:activate_policy_version',
              'sa2020-lab-setup=sa2020.cli:setup_lab',
              'akau-lab-setup=akau.cli:setup_lab',
          ],
      },
      install_requires=['Click==7.0','edgegrid-python==1.1.1','jsonpath-ng==1.4.3',
                        'jsonschema==3.0.0','requests==2.20.0','six==1.11.0',
                        'urljoin==1.0.0','urllib3==1.26.5','PyYAML==5.1','jsonpath-ng==1.4.3'],
      description="Helper scripts for SA2020 class - CI/CD from Zero to Hero on Akamai Platform",
      long_description=readme)
