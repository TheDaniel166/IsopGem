import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface AlignInput {
    workspace_root: string;
    check_type?: string;
}

export interface AlignResult {
    check_type: string;
    misalignments: string[];
    details: string;
    status: string;
}

export class AlignTool implements vscode.LanguageModelTool<AlignInput> {
    public readonly name = 'sophia_align';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<AlignInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, check_type = 'all' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/align_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                check_type
            ]);

            if (stderr) {
                console.error('Align stderr:', stderr);
            }

            const result: AlignResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Alignment check failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<AlignInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Checking documentation alignment: ${options.input.check_type}`
        };
    }
}
