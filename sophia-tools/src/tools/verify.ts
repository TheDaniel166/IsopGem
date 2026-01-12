import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface VerifyInput {
    check_type: 'pillar_sovereignty' | 'ui_purity' | 'all';
    target_path?: string;
    workspace_root: string;
}

export interface Violation {
    file: string;
    line?: number;
    rule: string;
    description: string;
    severity: 'error' | 'warning';
}

export interface VerifyOutput {
    check_type: string;
    target: string;
    violations: Violation[];
    passed: boolean;
    summary: string;
}

export class VerifyTool implements vscode.LanguageModelTool<VerifyInput> {
    public readonly name = 'sophia_verify';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<VerifyInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { check_type, target_path = '', workspace_root } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/verify_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                check_type,
                target_path
            ]);

            if (stderr) {
                console.error('Verify stderr:', stderr);
            }

            const result: VerifyOutput = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Verify failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<VerifyInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        const checkName = options.input.check_type.replace('_', ' ');
        return {
            invocationMessage: `Verifying ${checkName}...`
        };
    }
}
