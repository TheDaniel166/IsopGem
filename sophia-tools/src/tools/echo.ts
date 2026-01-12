import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface EchoInput {
    workspace_root: string;
    concept?: string;
    scope?: string;
}

export interface SemanticDrift {
    concept: string;
    original_meaning: string;
    current_usage: string[];
    drift_type: string;
    severity: string;
    evidence: string[];
}

export interface EchoResult {
    concept: string;
    semantic_health: string;
    drifts_detected: SemanticDrift[];
    fractures: string[];
    recommendations: string[];
}

export class EchoTool implements vscode.LanguageModelTool<EchoInput> {
    public readonly name = 'sophia_echo';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<EchoInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, concept = 'all', scope = 'code' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/echo_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                concept,
                scope
            ]);

            if (stderr) {
                console.error('Echo stderr:', stderr);
            }

            const result: EchoResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Echo failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<EchoInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Detecting semantic drift: ${options.input.concept || 'all concepts'}`
        };
    }
}
