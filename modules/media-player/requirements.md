---
module: media-player
version: 1.3.0
---

# Media Player — Product Spec

> Dummy content. This spec exists to test the shared specs pipeline. It is not a real requirement set.

## 1. Summary

A reusable player that plays a video from a network or local location inside a host screen, with standard playback controls.

## 2. Requirements

| Rule | Requirement |
| ---- | ----------- |
| RULE-PLAYER-PLAY-001 | The module shall play a video from a location supplied by the host. |
| RULE-PLAYER-PLAY-002 | The module shall show standard playback controls: play and pause, seek and volume. |
| RULE-PLAYER-PLAY-003 | Playback shall not start until the user starts it, unless autoplay is on. |
| RULE-PLAYER-PLAY-004 | Playback shall pause when the player leaves the screen. |
| RULE-PLAYER-CFG-001 | The host shall be able to choose autoplay, muted start and loop. All three default to off. |

## 3. Acceptance Scenarios

**Scenario 1 — Play a video**
GIVEN a host screen supplies a reachable video location
WHEN the player is shown and the user starts playback
THEN the video plays with the standard controls available
Covers: RULE-PLAYER-PLAY-001, RULE-PLAYER-PLAY-002, RULE-PLAYER-PLAY-003

**Scenario 2 — Leaving the screen pauses**
GIVEN a video is playing
WHEN the player leaves the screen
THEN playback pauses
Covers: RULE-PLAYER-PLAY-004

**Scenario 3 — Defaults**
GIVEN the host sets no options
WHEN the player is shown
THEN autoplay, muted start and loop are all off
Covers: RULE-PLAYER-CFG-001
