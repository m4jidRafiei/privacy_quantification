import setuptools
import p_privacy_qt

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name=p_privacy_qt.__name__,
    version=p_privacy_qt.__version__,
    author=p_privacy_qt.__author__,
    author_email=p_privacy_qt.__author_email__,
    description="Quantifying privacy in process mining",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m4jidRafiei/privacy_quantification",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'multiset==2.1.1',
        'pm4py==1.2.10',
        'pandas>=0.24.2',
        'pyemd==0.5.1',
        'pyfpgrowth==1.0',
        'numpy>=1.18.1',
        'python_Levenshtein==0.12.0'
    ],
    project_urls={
        'Source': 'https://github.com/m4jidRafiei/privacy_quantification'
    }
)