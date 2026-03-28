"""
demo_pipeline.py — Demo script for the 4-agent fraud detection pipeline
"""

from monitor import MonitoringAgent


def main():
    """Run the complete 4-agent fraud detection pipeline demo."""
    print("🚀 Starting FraudFlow-AI 4-Agent Pipeline Demo")
    print("=" * 80)

    try:
        # Initialize and run the monitoring agent
        monitor = MonitoringAgent()

        # Stream transactions with a small delay for demo effect
        monitor.stream_transactions(delay=0.1)

        print("\n" + "=" * 80)
        print("🎉 Demo Complete!")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("• Real-time transaction monitoring")
        print("• Multi-pattern fraud detection")
        print("• Risk-based decision making")
        print("• FIU-ready evidence generation")
        print("• Automated account blocking simulation")

        # Show innovation moment
        print("\n💡 INNOVATION MOMENT:")
        print("\"This evidence JSON can be directly submitted to the Financial Intelligence Unit.\"")
        print("\"We don't just detect - we document!\"")

    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return 1

    return 0


if __name__ == '__main__':
    main()