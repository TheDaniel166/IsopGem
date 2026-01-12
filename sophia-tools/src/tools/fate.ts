import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface FateInput {
    workspace_root: string;
    target?: string;
    horizon?: string;
}

export interface FateWarning {
    type: string;
    target: string;
    inevitability: string;
    evidence: string[];
    entropy_score: number;
}

export interface FateResult {
    target: string;
    horizon: string;
    warnings: FateWarning[];
    structural_health: number;
    summary: string;
}

export class FateTool implements vscode.LanguageModelTool<FateInput> {
    public readonly name = 'sophia_fate';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<FateInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, target = 'src', horizon = 'medium' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/fate_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                target,
                horizon
            ]);

            if (stderr) {
                console.error('Fate stderr:', stderr);
            }

            const result: FateResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Fate reading failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<FateInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Reading structural fate: ${options.input.target || 'workspace'}`
        };
    }
}
