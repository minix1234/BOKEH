# importing modules from parent folder - best practices
# As taken from
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder/50194143#50194143
# also see
# https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944


from setuptools import setup, find_packages

setup(name='openet', version='0.1', packages=find_packages())