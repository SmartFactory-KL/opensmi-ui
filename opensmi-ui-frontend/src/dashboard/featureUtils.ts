import type { EntityNode } from "@/types/NodeFeatureTypes";

export function getFeatureName(feature: EntityNode): string {
    return (
        feature.entity?.name ||
        feature.opcNode?.displayName?.text ||
        feature.opcNode?.browseName?.name ||
        feature.entityId
    );
}

export function getFeatureType(feature: EntityNode): string {
    return feature.entityType ?? "Unknown";
}
