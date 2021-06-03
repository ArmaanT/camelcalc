import dedent from 'ts-dedent';
import { Construct } from "constructs";
import { App, CheckoutJob, Stack, Workflow } from "cdkactions";

export class CamelCalcStack extends Stack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    // define workflows here
    const workflow = new Workflow(this, 'build-and-publish', {
      on: {
        push: {
          branches: ['**'],
          tags: ['[0-9]+.[0-9]+.[0-9]+'],
        },
      },
      name: 'Build and Publish',
    });

    const testJob = new CheckoutJob(workflow, 'test', {
      runsOn: 'ubuntu-latest',
      container: {
        image: `python:3.9`,
      },
      steps: [
        {
          name: 'Install dependencies',
          run: dedent`pip install poetry
          poetry install`,
        },
        {
          name: 'Lint',
          run: dedent`poetry run flake8 .
          poetry run black --check .
          poetry run mypy --strict .`
        }
      ],
    });
    new CheckoutJob(workflow, 'publish', {
      runsOn: 'ubuntu-latest',
      container: {
        image: `python:3.9`,
      },
      needs: testJob.id,
      if: "startsWith(github.ref, 'refs/tags')",
      steps: [
        {
          name: 'Install poetry',
          run: 'pip install poetry',
        },
        {
          name: 'Build',
          run: 'poetry build',
        },
        {
          name: 'Configure poetry',
          run: 'poetry config pypi-token.pypi ${{ secrets.PYPI_TOKEN }}',
        },
        {
          name: 'Publish',
          run: 'poetry publish',
        },
      ],
    });
  }
}

const app = new App();
new CamelCalcStack(app, 'cdk');
app.synth();
