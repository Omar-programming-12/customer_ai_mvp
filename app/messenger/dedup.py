processed_message_ids: set[str] = set()


def already_processed(message_id: str) -> bool:

    if not message_id:
        return False

    if message_id in processed_message_ids:
        return True

    processed_message_ids.add(message_id)

    # Keep memory small for MVP
    if len(processed_message_ids) > 1000:
        oldest_message_id = next(
            iter(processed_message_ids)
        )

        processed_message_ids.remove(
            oldest_message_id
        )

    return False
