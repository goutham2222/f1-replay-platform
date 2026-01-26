# ADR-001: Core Architecture Decisions for F1 Replay Platform

## Status
Accepted

## Context
The F1 Replay Platform is designed to replay historical Formula 1 races using event-time simulation, distributed processing, and cloud-native analytics. The system must support:

- Time-aligned telemetry processing
- Deterministic replay
- Scalable ETL
- Interactive visualization
- Low operational overhead
- Interview-grade architectural clarity

## Decisions

### 1. Event-Time Lakehouse over Traditional Data Warehouse

We model all data using an event-time axis (milliseconds since race start) rather than star-schema facts and dimensions.

**Rationale:**
- Replay and simulation require continuous time alignment
- Enables interpolation, windowing, and deterministic state reconstruction
- Matches streaming system design patterns (Flink / Spark Structured Streaming)

---

### 2. AWS Glue (Spark) over EMR or Pandas

Glue is chosen as the distributed processing engine.

**Rationale:**
- Native Spark with serverless execution
- Tight integration with S3 and Glue Catalog
- Supports window functions, time alignment, interpolation
- Zero cluster management (vs EMR)
- Production-grade ETL credibility for interviews

---

### 3. S3 + Athena over Redshift (Phase 1)

The lakehouse uses Parquet on S3 with Athena for SQL.

**Rationale:**
- Decoupled storage and compute
- Serverless query layer
- Cost efficient for batch analytics
- Sufficient for replay frame validation and debugging
- Redshift may be introduced later for low-latency BI if needed

---

### 4. ECS Fargate over EC2 or EKS

Replay API and UI run on ECS Fargate.

**Rationale:**
- No server management
- Native ALB integration
- Simpler than Kubernetes for single-team project
- Production-grade container orchestration
- Supports auto-scaling and isolation

---

### 5. FastAPI for Replay Engine

FastAPI is used for the simulation and serving layer.

**Rationale:**
- Async support
- High performance
- Native Python integration with Spark outputs
- Clean OpenAPI interface for UI

---

### 6. Streamlit for Visualization

Streamlit is used for the interactive replay UI.

**Rationale:**
- Python-native
- Rapid development
- Sufficient for animation and telemetry visualization
- Avoids frontend framework overhead
- Cost efficient (no GPU, no WebGL)

---

### 7. No Lambda in Initial Architecture

The system uses batch ingestion and Spark processing, not event-triggered Lambda pipelines.

**Rationale:**
- Replay is historical and batch-oriented
- Spark windowing requires full-session context
- Simplifies architecture
- Lambda may be added later for near-real-time ingestion

---

### 8. Infrastructure as Code using AWS CDK

All infrastructure is defined in CDK (Python).

**Rationale:**
- Strong typing
- Versioned architecture
- Interview-grade reproducibility
- Easier than Terraform for complex AWS graphs
