from __future__ import annotations

import re
from typing import Any


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"不支持的 JSON Schema type：{expected}")


def _resolve_local_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"只支持本地 JSON Schema $ref：{ref}")
    current: Any = root
    for raw in ref[2:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        current = current[key]
    if not isinstance(current, dict):
        raise ValueError(f"$ref 未指向 Schema 对象：{ref}")
    return current


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    *,
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
) -> list[str]:
    """Validate the deterministic JSON Schema subset used by CatDrama V4.1."""
    root = root_schema or schema

    if "$ref" in schema:
        return validate_instance(
            instance,
            _resolve_local_ref(root, schema["$ref"]),
            root_schema=root,
            path=path,
        )

    if "anyOf" in schema:
        branches = [
            validate_instance(instance, option, root_schema=root, path=path)
            for option in schema["anyOf"]
        ]
        if any(not branch for branch in branches):
            return []
        return [f"{path}: 不符合 anyOf 中的任何合同"]

    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        if not any(_type_matches(instance, item) for item in expected_types):
            errors.append(
                f"{path}: 类型应为 {' | '.join(expected_types)}，实际为 "
                f"{type(instance).__name__}"
            )
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: 必须等于 {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: 非法枚举值 {instance!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: 字符串长度小于 {schema['minLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: 不匹配 pattern {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: 小于 minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: 大于 maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: 项目数小于 {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(
                    validate_instance(
                        item,
                        item_schema,
                        root_schema=root,
                        path=f"{path}[{index}]",
                    )
                )

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: 缺少必填字段 {key}")

        properties = schema.get("properties", {})
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(
                    validate_instance(
                        value,
                        properties[key],
                        root_schema=root,
                        path=child_path,
                    )
                )
                continue

            additional = schema.get("additionalProperties", True)
            if additional is False:
                errors.append(f"{child_path}: 不允许额外字段")
            elif isinstance(additional, dict):
                errors.extend(
                    validate_instance(
                        value,
                        additional,
                        root_schema=root,
                        path=child_path,
                    )
                )

    return errors


def assert_valid(instance: Any, schema: dict[str, Any], schema_name: str) -> None:
    errors = validate_instance(instance, schema)
    if errors:
        raise ValueError(
            f"{schema_name} Validation Failed:\n- " + "\n- ".join(errors)
        )
