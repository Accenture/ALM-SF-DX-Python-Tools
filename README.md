# Salesforce ALM Framework - Python Scripts for DX

Python scripts to perform ALM (Application Lifecycle Management) operations over Salesforce platform using metadata DX. The Metadata API version can be found at [ALM-SF-Metadata-API-Python-Tools](https://github.com/Accenture/ALM-SF-Metadata-API-Python-Tools).

These scripts can be used standalone or invoked from CI/CD pipelines, such as the Jenkins pipelines from [ALM-SF-DX-Pipelines](https://github.com/Accenture/ALM-SF-DX-Pipelines).

## Call Git Server

Handle Git operations between several Git distributions.

Currently supporting:
- Gitlab
- Bitbucket Cloud 
- Bitbucket Server

Detailed explanation can be found at [Call Git Server README](/callGitServer/README.md).

## Generate Package

Creates a package.xml from a JSON.

Detailed explanation can be found at [Geneerate Package README](/generatePackage/README.md).

## Merge Metadata

Merges splitted components into destination metadata. Instead of comparing two files, this script can be used to automatically merge a retrieved package with individual components, such as Assignment Rules, Custom Labels, Sharing Rules, .. or Profile permissions.

Detailed explanation can be found at [Merge Metadata README](/mergeMetadata/README.md).

## MergerDx

Builds a package with differences between source and target branches or commits.

Detailed explanation can be found at [Merger README](/merger/README.md).

## PMD

Creates a customizable report from a PMD analysis.

Detailed explanation can be found at [PMD README](/pmd/README.md).

## Send Email

Sends an email showing the pipeline results and attaches PMD and/or deployment logs.

Detailed explanation can be found at [Send email README](/sendemail/README.md).

# Contributors Guide

## Contribution

We encourage you to contribute to new features or fixes. You can start by opening a
[Github issue](https://github.com/Accenture/ALM-SF-DX-Python-Tools/issues) to get feedback from other contributors.

## License

The Salesforce ALM Framework is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) for details.
