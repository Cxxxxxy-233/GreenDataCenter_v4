"""
Command line interface (based on LangGraph - Simplified version)
"""

import json
import sys
from pathlib import Path
from typing import Any

import typer

from greendatacenter.coordinator_v2 import AISystemCoordinator

app = typer.Typer(help="GreenDataCenter - Data Center Design System (v2.0 LangGraph)")
console = None  # We'll use typer.echo instead


@app.command()
def generate(
    input_file: Path = typer.Argument(..., help="Requirement input file (JSON format)"),
    output_file: Path = typer.Option(None, "--output-file", "-o", help="Output file (JSON format)"),
    detail: str = typer.Option("summary", "--detail", "-d", help="Detail level: summary/detail/full")
):
    """
    Generate data center construction solution

    Examples:
        gdc generate input.json -o output.json
        gdc generate input.json --detail full
    """
    try:
        # Read input file
        typer.echo(f"Reading input file: {input_file}")
        input_data = json.loads(input_file.read_text(encoding="utf-8"))

        # Create coordinator
        coordinator = AISystemCoordinator()

        # Generate solution
        typer.echo("Generating solution...")
        result = coordinator.generate_solution(input_data=input_data)

        # Display result
        if result.get("success"):
            solution = result.get("solution", {})
            streaming_output = result.get("streaming_output", [])

            # Show streaming output
            if streaming_output:
                typer.echo("\n=== Expert Dialogue History ===\n")
                for msg in streaming_output:
                    node_type = msg.get("node", "unknown")
                    expert = msg.get("expert", "unknown")
                    content = msg.get("content", "")
                    typer.echo(f"[{node_type}] {expert}: {content}")

            # Show solution summary
            typer.echo(f"\n=== Solution Summary ===")
            typer.echo(f"Name: {solution.get('name', 'N/A')}")
            typer.echo(f"Overall Score: {solution.get('overall_scores', {}).get('overall', 0):.2f}")
            typer.echo(f"Confidence: {solution.get('confidence', 0.8):.2f}")

            # Show key metrics
            if solution.get("key_metrics"):
                metrics = solution["key_metrics"]
                typer.echo(f"\nKey Metrics:")
                typer.echo(f"  Total Cost: {metrics.get('total_cost', 0):.1f}万元")
                typer.echo(f"  PUE: {metrics.get('pue', 0)}")
                typer.echo(f"  Green Power Ratio: {metrics.get('green_power_ratio', 0)*100:.0f}%")
                typer.echo(f"  Tier Level: {metrics.get('tier_level', 0)}")
                typer.echo(f"  Expected Availability: {metrics.get('expected_availability', 0):.1f}%")
                typer.echo(f"  Annual Carbon Emission: {metrics.get('annual_carbon_emission', 0):.1f}t")

            # Save output file
            if output_file:
                output_file.write_text(
                    json.dumps(solution, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                typer.echo(f"\nSolution saved to: {output_file}")
        else:
            typer.echo(f"Error: {result.get('error', 'Unknown error')}")

    except FileNotFoundError:
        typer.echo(f"Error: File not found - {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: JSON parsing failed - {e}")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@app.command()
def status():
    """Show system status"""
    coordinator = AISystemCoordinator()
    system_status = coordinator.get_system_status()

    typer.echo("=== System Status ===\n")

    # Coordinator status
    typer.echo("Coordinator:")
    for key, value in system_status["coordinator"].items():
        typer.echo(f"  {key}: {value}")

    # Graph status
    graph_status = system_status["graph"]
    typer.echo(f"\nGraph:")
    typer.echo(f"  Nodes: {len(graph_status['nodes'])}")
    typer.echo(f"  Edges: {graph_status['edges_count']}")
    typer.echo(f"  Node List: {', '.join(graph_status['nodes'][:5])}")

    # Memory status
    memory_status = system_status["memory"]
    typer.echo(f"\nMemory:")
    typer.echo(f"  Type: {memory_status['type']}")
    typer.echo(f"  History Length: {memory_status['history_length']}")
    typer.echo(f"  Has Summary: {'Yes' if memory_status['has_summary'] else 'No'}")


@app.command()
def example():
    """Generate example input file"""
    example_data = {
        "name": "华东某数据中心一期建设",
        "description": "建设100个机柜的数据中心",
        "rack_count": 100,
        "total_power": 500,
        "power_density": 5,
        "tier_level": 3,
        "pue_target": 1.3,
        "floor_area": 500,
        "green_power_ratio": 0.7,
        "budget": 2000,
        "bandwidth": 1000,
        "objectives": ["降低PUE", "提高可靠性", "控制成本"],
        "constraints": ["预算2000万元", "场地500m²"],
        "priorities": {
            "economic": 3,
            "reliability": 5,
            "environmental": 4
        }
    }

    output_file = Path("example_input.json")
    output_file.write_text(
        json.dumps(example_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    typer.echo(f"Example file generated: {output_file}")
    typer.echo("\nUsage:")
    typer.echo("  gdc generate example_input.json")


@app.command()
def explain(
    solution_file: Path = typer.Argument(..., help="Solution file (JSON format)"),
    detail: str = typer.Option("summary", "--detail", "-d", help="Detail level: summary/detail/full")
):
    """
    Explain construction solution

    Examples:
        gdc explain solution.json
        gdc explain solution.json --detail full
    """
    try:
        # Read solution file
        solution_data = json.loads(solution_file.read_text(encoding="utf-8"))

        # Create coordinator
        coordinator = AISystemCoordinator()

        # Explain solution
        explanation = coordinator.explain_solution(solution_data, detail)

        # Show explanation
        typer.echo(explanation)

    except FileNotFoundError:
        typer.echo(f"Error: File not found - {solution_file}")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}")
        sys.exit(1)


def main():
    """Main function"""
    app()


if __name__ == "__main__":
    main()
