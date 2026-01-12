import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface SealInput {
    workspace_root: string;
    seal_name: string;
}

export interface SealResult {
    seal: string;
    passed: boolean;
    violations: string[];
    details: string;
}

export class SealTool implements vscode.LanguageModelTool<SealInput> {
    public readonly name = 'sophia_seal';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<SealInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, seal_name } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/seal_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                seal_name
            ]);

            if (stderr) {
                console.error('Seal stderr:', stderr);
            }

            const result: SealResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Seal verification failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<SealInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Verifying Seal: ${options.input.seal_name}`
        };
    }
}
