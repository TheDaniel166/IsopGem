import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface TraceInput {
    workspace_root: string;
    target: string;
    trace_type?: string;
}

export interface TraceResult {
    target: string;
    dependencies: string[];
    dependents: string[];
    import_graph: Record<string, string[]>;
}

export class TraceTool implements vscode.LanguageModelTool<TraceInput> {
    public readonly name = 'sophia_trace';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<TraceInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, target, trace_type = 'both' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/trace_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                target,
                trace_type
            ]);

            if (stderr) {
                console.error('Trace stderr:', stderr);
            }

            const result: TraceResult = JSON.parse(stdout);

            return {
                content: [
                    new vscode.LanguageModelTextPart(JSON.stringify(result, null, 2))
                ]
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            return {
                content: [
                    new vscode.LanguageModelTextPart(
                        JSON.stringify({ error: `Trace failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<TraceInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Tracing dependencies for: ${options.input.target}`
        };
    }
}
