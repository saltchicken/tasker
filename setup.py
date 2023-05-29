import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name='tasker',
    version='0.0.7',
    author='John Eicher',
    author_email='john.eicher89@gmail.com',
    description='Testing installation of Package',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url='https://github.com/saltchicken/tasker',
    # project_urls = {
    #     "Bug Tracker": "https://github.com/saltchicken/tasker/issues"
    # },
    # license='MIT',
    py_modules=['tasker'],
    install_requires=['pyqt5', 'torch', 'torchvision', 'torchaudio',
                     'screen_writer @ git+https://github.com/saltchicken/screen_writer.git@master#egg=screen_writer',
                     'vad_logger @ git+https://github.com/saltchicken/vad_logger.git@master#egg=vad_logger',
                     'transcriber @ git+https://github.com/saltchicken/transcriber.git@master#egg=transcriber'],
)
