import re
from typing import Any, Callable

EndpointType = tuple[str, str, str, Callable[..., Any]]

HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head", "trace")


def preprocessor_hook(endpoints: list[EndpointType]) -> list[EndpointType]:
    """This is used to restrict drf-spectacular to only v2 entrypoints"""
    filtered = []
    for path, path_regex, method, callback in endpoints:
        if path.startswith("/api/v2"):
            filtered.append((path, path_regex, method, callback))
    return filtered


def _ensure_operation_ids(paths: dict[str, Any]) -> None:
    """Ensure every operation in paths has an operationId (required by drf-spectacular)."""
    for path, path_spec in paths.items():
        if not isinstance(path_spec, dict):
            continue
        for method in HTTP_METHODS:
            operation = path_spec.get(method)
            if isinstance(operation, dict) and "operationId" not in operation:
                # Generate an operationId from the path and method
                clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                operation["operationId"] = f"allauth_{method}_{clean_path}"


def _prefix_refs(obj: Any, renames: dict[str, str]) -> Any:
    """Recursively rename $ref values in an OpenAPI spec object."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                for old_name, new_name in renames.items():
                    value = re.sub(
                        rf"(#/components/\w+/){re.escape(old_name)}$",
                        rf"\1{new_name}",
                        value,
                    )
                result[key] = value
            else:
                result[key] = _prefix_refs(value, renames)
        return result
    elif isinstance(obj, list):
        return [_prefix_refs(item, renames) for item in obj]
    return obj


def merge_allauth_spec(result: dict[str, Any], generator: Any, request: Any, public: bool) -> dict[str, Any]:
    """Merge allauth headless OpenAPI spec into drf-spectacular output.

    Prefixes conflicting allauth component names with "Allauth" to avoid
    overwriting DRF-generated schemas (e.g. allauth's "User" vs DRF's "User").
    """
    from allauth.headless.spec.internal.schema import get_schema

    allauth_spec = get_schema()

    # Find conflicting component names across all component types
    renames: dict[str, str] = {}
    allauth_components = allauth_spec.get("components", {})
    result_components = result.setdefault("components", {})
    for component_type, component_values in allauth_components.items():
        if not isinstance(component_values, dict):
            continue
        existing = result_components.get(component_type, {})
        for name in component_values:
            if name in existing:
                renames[name] = f"Allauth{name}"

    # Apply renames to allauth spec (paths and components)
    if renames:
        allauth_spec = _prefix_refs(allauth_spec, renames)
        for component_type in list(allauth_spec.get("components", {}).keys()):
            section = allauth_spec["components"][component_type]
            if isinstance(section, dict):
                renamed_section = {}
                for name, value in section.items():
                    renamed_section[renames.get(name, name)] = value
                allauth_spec["components"][component_type] = renamed_section

    # Merge paths
    allauth_paths = allauth_spec.get("paths", {})
    _ensure_operation_ids(allauth_paths)
    result.setdefault("paths", {}).update(allauth_paths)

    # Merge all component types (schemas, responses, parameters, etc.)
    allauth_components = allauth_spec.get("components", {})
    for component_type, component_values in allauth_components.items():
        if isinstance(component_values, dict):
            result_components.setdefault(component_type, {}).update(component_values)

    return result
