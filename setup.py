from setuptools import find_packages, setup
from wgse.VERSION import VERSION

DEPENDENCIES = [
    "setuptools",
    "pefile",
    "pycurl",
    "tqdm",
    "google-cloud-storage",
    "sphinx",
    "pytest",
    "pyqt6",
    "pyinstaller",
    "PySide6",
    "jinja2",
    "vcf_parser",
    "WGSE-NG-3rd-party",
]

setup(
    name="WGSE-NG",
    packages=find_packages(include=["wgse", "wgse.*"]),
    author="Multiple",
    author_email="",
    include_package_data=True,
    package_data={
        "wgse.mtDNA": ["*.*"],
        "wgse.metadata": ["*.*"],
        "wgse.metadata.microarray_templates.head": ["*.*"],
        "wgse.metadata.microarray_templates.body": ["*.*"],
        "wgse.metadata.bed_templates": ["*.*"],
        "wgse.metadata.report_templates": ["*.*"],
    },
    description="Whole Genome Sequencing data manipulation tool",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=DEPENDENCIES,
    url="https://github.com/WGSE-NG/WGSE-NG",
    version=VERSION,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    entry_points={
        "gui_scripts": [
            "wgse = wgse.main:main",
        ]
    },
    keywords=["bioinformatics", "genetics", "wgs", "microarray", "science"],
)
