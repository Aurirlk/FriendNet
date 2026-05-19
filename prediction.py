"""Feature prediction from friends (homophily-style majority vote)."""

from __future__ import annotations

from collections import Counter

from relationships import _direct_friends


def _second_degree(individual: str, bestie_dict: dict[str, set[str]]) -> set[str]:
    """Friends-of-friends: exclude self and direct friends (same scope as friend_second_besties)."""
    direct = _direct_friends(individual, bestie_dict)
    second: set[str] = set()
    for f in direct:
        second |= _direct_friends(f, bestie_dict)
    second.discard(individual)
    second -= direct
    return second


def _feature_observations(
    users: set[str],
    feature: str,
    feat_dict: dict[str, dict[str, str]],
    unknown_user: str,
) -> list[str]:
    """Values for `feature` among users who explicitly have that key (including '')."""
    obs: list[str] = []
    for uid in users:
        if uid == unknown_user:
            continue
        attrs = feat_dict.get(uid)
        if not attrs or feature not in attrs:
            continue
        obs.append(attrs[feature])
    return obs


def _majority_sorted(obs: list[str]) -> list[str]:
    """Labels with highest frequency; ties broken by sorted order of those labels."""
    if not obs:
        return []
    counts = Counter(obs)
    top = max(counts.values())
    return sorted(k for k, v in counts.items() if v == top)


def friendly_prediction(
    unknown_user: str,
    features,
    bestie_dict: dict[str, set[str]],
    feat_dict: dict[str, dict[str, str]],
) -> dict[str, list[str]]:
    """
    For each feature (screenshot 5 — bonus):
    1) Among direct friends only, take the most common attribute value in feat_dict;
       ties → sorted list of all tied values.
    2) If no direct friend has that feature key, repeat using second-degree friends.

    Ignores feat_dict[unknown_user]. Missing keys mean unknown; '' is a real value.
    Feature keys in the result follow sorted(features).
    """
    direct = _direct_friends(unknown_user, bestie_dict)
    second = _second_degree(unknown_user, bestie_dict)
    result: dict[str, list[str]] = {}

    for feat in sorted(features):
        obs1 = _feature_observations(direct, feat, feat_dict, unknown_user)
        if obs1:
            result[feat] = _majority_sorted(obs1)
            continue
        obs2 = _feature_observations(second, feat, feat_dict, unknown_user)
        result[feat] = _majority_sorted(obs2)

    return result
