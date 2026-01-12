import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface ResearchInput {
    workspace_root: string;
    question: string;
    depth?: string;
}

export interface ResearchResult {
    question: string;
    investigation_steps: string[];
    findings: Record<string, any>;
    root_cause: string;
    recommendations: string[];
    confidence: string;
}

export class ResearchTool implements vscode.LanguageModelTool<ResearchInput> {
    public readonly name = 'sophia_research';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<ResearchInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, question, depth = 'standard' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/research_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                question,
                depth
            ]);

            if (stderr) {
                console.error('Research stderr:', stderr);
            }

            const result: ResearchResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Research failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<ResearchInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Investigating: ${options.input.question}`
        };
    }
}
