from setuptools import setup

setup(name='cbpi4_OWserverTemps',
      version='0.0.1',
      description='CraftBeerPi Plugin',
      author='Andrew Cooper',
      author_email='squamishcoop@gmail.com',
      url='',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_OWserverTemps': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_OWserverTemps'],
     )