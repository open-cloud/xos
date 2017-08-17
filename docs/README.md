# Models for CORD

XOS implements a model-based service control plane for CORD.
This guide describes the how models are expressed in XOS and
documents the toolchain used to auto-generate various
elements of CORD from these models.

It also describes the role of Synchronizers in bridging the CORD data
model with the backend components (e.g., VNFs, micro-services,
SDN control apps) that implement CORD's service data plane.

