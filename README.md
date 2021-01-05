[![Build Status](https://github.com/salilab/cryptosite-web/workflows/build/badge.svg?branch=main)](https://github.com/salilab/cryptosite-web/actions?query=workflow%3Abuild)
[![codecov](https://codecov.io/gh/salilab/cryptosite-web/branch/main/graph/badge.svg)](https://codecov.io/gh/salilab/cryptosite-web)
[![Code Climate](https://codeclimate.com/github/salilab/cryptosite-web/badges/gpa.svg)](https://codeclimate.com/github/salilab/cryptosite-web)

This is the source code for [CryptoSite](https://salilab.org/cryptosite/), a web
service for predicting the location of cryptic binding sites in proteins and
protein complexes.
It uses the [Sali lab web framework](https://github.com/salilab/saliweb/).

See [P. Cimermancic et al., J Mol Biol, (2016) 428, 709-19](https://www.ncbi.nlm.nih.gov/pubmed/26854760) for details.

# Setup

First, install and set up the
[Sali lab web framework](https://github.com/salilab/saliweb/) and the
base [CryptoSite library](https://github.com/salilab/cryptosite/).

The web service expects to find a `cryptosite` [module](http://modules.sourceforge.net/),
i.e. it runs `module load cryptosite`. This module should put the CryptoSite
scripts from that library in the system PATH. The library is used by all
parts of the web service, including jobs that run on the cluster, so it must be
installed on a network filesystem that is visible to all nodes.
