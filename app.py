from orchestrator.release_orchestrator import ReleaseOrchestrator


def main():
    orchestrator = ReleaseOrchestrator()

    state = orchestrator.run()

    print("\n=== RELEASE FINDINGS ===")
    print(state.findings)

    print("\n=== EVENT LOG ===")
    for event in state.events:
        print(event)


if __name__ == "__main__":
    main()