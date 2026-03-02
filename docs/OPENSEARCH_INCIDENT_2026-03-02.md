# OpenSearch Cluster Red Incident (2026-03-02)

## Summary
On March 2, 2026, the `/search` dashboard in production showed OpenSearch cluster status as `red`.
The RAG API health response confirmed:
- overall service status was `healthy`
- OpenSearch service status was `healthy`
- OpenSearch `cluster_status` was `red`

## Impact
- Portal health card displayed OpenSearch as red.
- RAG `documents` index remained available and green, but cluster-level health was degraded by one unassigned primary shard.

## Root Cause
- One unassigned primary shard in index `.opensearch-sap-log-types-config`.
- Allocation explain showed `no_valid_shard_copy` and index corruption:
  - `corrupt_index_exception`
  - Lucene file `_24.nvm` was `0 bytes` (invalid/corrupt shard store)
- Data path was mounted on CIFS/Azure Files (`//intaktstorage.file.core.windows.net/...`), which is a known risk for Lucene/OpenSearch index integrity and latency-sensitive metadata operations.

## What We Did Today
1. Confirmed cluster status and shard state:
   - `_cluster/health` returned `red` with `unassigned_shards: 1`.
   - `_cat/shards` identified `.opensearch-sap-log-types-config` shard `0` primary as `UNASSIGNED`.
2. Confirmed exact allocation failure:
   - `_cluster/allocation/explain` reported `no_valid_shard_copy` and corruption.
3. Remediated immediately:
   - Deleted corrupted non-critical plugin index `.opensearch-sap-log-types-config`.
   - Cluster returned to `green` (`unassigned_shards: 0`).
4. Reduced recurrence risk at runtime:
   - Set persistent cluster settings:
     - `plugins.security_analytics.alert_history_enabled=false`
     - `plugins.security_analytics.alert_finding_enabled=false`

## Current Status
- OpenSearch cluster health: `green`
- Unassigned shards: `0`
- `documents` index: healthy

## Recommendations
1. **Storage**: Move OpenSearch data from Azure Files/CIFS to block storage (e.g., Azure Disk) for Lucene reliability.
2. **Plugin hardening**: Remove/disable unused plugins (especially Security Analytics/SAP) in the OpenSearch image/config so disabled features do not recreate fragile system indices.
3. **Host tuning**: Ensure `vm.max_map_count >= 262144` in the runtime environment.
4. **Monitoring**: Alert on:
   - `_cluster/health.status != green`
   - `unassigned_shards > 0`
   - `corrupt_index_exception` in OpenSearch logs
5. **Runbook**: Keep this recovery sequence documented:
   - identify unassigned shard
   - run allocation explain
   - if non-critical corrupted system index, delete and verify cluster health
