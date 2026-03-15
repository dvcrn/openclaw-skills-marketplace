# xuexitong

## Use this file when

The current task is on Xuexitong / Chaoxing

## Default profile

Use profile:

```bash
xuexitong
```

## Site
`https://i.chaoxing.com/`

## Behavior

- Do not enter a full-screen homework page.
- Do not perform actions that a normal user could not perform.
- Submit the answers in the same way a normal user would.
- A confirmation dialog may appear and require one more click to complete the submission.
- Before submitting, briefly check whether the answers have actually been selected.
- Do not attempt to redo it unless the user explicitly asks.

## Chapter quiz

For chapter quizzes opened inside `studentstudy`, do not search the whole outer page blindly.
The outer page usually only shows the shell and tab bar.
The real questions are normally three layers deep:

1. outer page: `/mycourse/studentstudy`
2. main content iframe: `#iframe` → usually `/mooc-ans/knowledge/cards`
3. work wrapper iframe inside that page: usually an iframe whose `src` contains `/ananas/modules/work/index.html`
4. real quiz iframe inside the wrapper: `#frame_content` → usually `/mooc-ans/work/doHomeWorkNew...`

Once the real quiz iframe is found, stop exploring the outer shell.
Prefer one larger DOM read inside the innermost document over many tiny probe steps.

Use this fast order:

1. enter `#iframe`
2. find the work wrapper iframe
3. enter `#frame_content`
4. read the innermost document in one pass

Inside the innermost document, prefer these targets:

- quiz status: `.testTit_status`, `.newTestTitle`, `.achievement`
- title block: `.ceyan_name`
- form: `#form1`
- normalized question blocks: `#form1 .TiMu.newTiMu`
- fallback question blocks only if needed: `#form1 .singleQuesId`
- stem: `.Zy_TItle`
- options: `li.font-cxsecret.before-after`
- option marker and value carrier: `.num_option`
- answer input: `#answer<questionId>`
- answer type: `#answertype<questionId>`
- submit trigger: `a.btnSubmit` or page function `btnBlueSubmit()`

Important details:

- `.TiMu.newTiMu` is usually the real readable block. `.singleQuesId` often mirrors the same question and can cause duplicate counting.
- Do not judge selection only by visible highlight classes. Prefer checking whether the hidden answer input `#answer<questionId>` was updated. For many choice questions, the chosen option also gets class `check_answer`.
- For judgment questions, the visible labels may be `A/B`, but the actual option values are often `.num_option[data="true"]` and `.num_option[data="false"]` for `对/错`.
- Before submitting, briefly verify that each intended answer is already reflected in the corresponding hidden answer input.

Submission flow:

1. trigger the innermost page submit control
2. if needed, call the page's native submit path rather than inventing a custom flow
3. confirm the outer dialog, usually top document `#popok`
4. verify success from the result page, usually by one of:
   - URL containing `selectWorkQuestionYiPiYue`
   - status text `已完成`
   - score text such as `本次成绩`

After submission, do not keep re-scanning the directory or outer shell if the result page already clearly shows completion.

## Text obfuscation

- If the text is obfuscated or appears as garbled pseudo-Chinese, infer the intended meaning directly and don't taking a screenshot.

For example

```text
运用阶媺分析媻来判断媹嫀我们的朋友、媹嫀我们的敌人,对于革命至关重要。以下哪本隗嫀马克思媾义阶媺分析媻的经典?
A
《嫅国媯偸嫄媭媺的分嫃》
B
《嫇嫆论》
C
《嫉嫈论》
D
《嫏南溓裊嫎媥嫊察报嫍》
```

can infer to:

```text
运用阶级分析法来判断谁是我们的朋友、谁是我们的敌人，对于革命至关重要。以下哪本书是马克思主义阶级分析法的经典？

选项：
- A 《中国社会各阶级的分析》
- B 《矛盾论》
- C 《实践论》
- D 《湖南农民运动考察报告》
```

## Note

It is normal for an AI assistant to make mistakes on some questions.
