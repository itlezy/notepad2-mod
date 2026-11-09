// Exercises production MRU/path functions, plus compiler and startup contracts.
#include <windows.h>
#include <shlwapi.h>
#include <stdio.h>
#include "Scintilla.h"
#include "Helpers.h"
#include "Version.h"
#include "fork-contracts.h"

HINSTANCE g_hInstance;
UINT16 g_uWinVer;
HMODULE hModUxTheme;
WCHAR szIniFile[MAX_PATH];

#define CHECK(condition) do { if (!(condition)) { printf("Failed at line %d\n",__LINE__); return 1; } } while (0)

int main(void)
{
  WCHAR path[MAX_PATH],second[MAX_PATH],relative[] = L"test-file.txt";
  LPMRULIST list = MRU_Create(L"Test",MRU_NOCASE,3);
  STARTUPINFO si = {0};
  int i;
  g_hInstance = GetModuleHandle(NULL);
  GetModuleFileName(NULL,path,MAX_PATH);
  PathRemoveFileSpec(path);
  lstrcpy(second,path);
  PathAppend(path,L"test-file.txt");
  PathAppend(second,L"second.txt");
  CHECK(MRU_AddFile(list,path,FALSE,FALSE)); // Initially every slot is NULL.
  CHECK(lstrcmpi(list->pszItems[0],path) == 0);
  CHECK(MRU_AddFile(list,second,FALSE,FALSE)); // Partial list.
  CHECK(MRU_AddFile(list,path,FALSE,FALSE)); // Existing absolute duplicate.
  CHECK(lstrcmpi(list->pszItems[0],path) == 0 && lstrcmpi(list->pszItems[1],second) == 0);
  MRU_Empty(list);
  list->pszItems[1] = StrDup(relative); // Null gap before a relative duplicate.
  CHECK(MRU_AddFile(list,path,FALSE,FALSE));
  CHECK(lstrcmpi(list->pszItems[0],path) == 0);
  MRU_Empty(list);
  SetEnvironmentVariable(L"NP2_MRU_TEST",second);
  list->pszItems[1] = StrDup(L"%NP2_MRU_TEST%");
  CHECK(MRU_AddFile(list,second,FALSE,FALSE));
  CHECK(lstrcmpi(list->pszItems[0],second) == 0);
  MRU_Empty(list);
  for (i = 0; i < 5; ++i) {
    WCHAR name[MAX_PATH];
    wsprintf(name,L"C:\\test-%d.txt",i);
    CHECK(MRU_AddFile(list,name,FALSE,FALSE));
  }
  CHECK(lstrcmp(list->pszItems[0],L"C:\\test-4.txt") == 0);
  CHECK(lstrcmp(list->pszItems[2],L"C:\\test-2.txt") == 0);
  MRU_Destroy(list);
  CHECK(VERSION_LEGALCOPYRIGHT_LONG[0] == 0x00A9);
  CHECK(wcschr(titlePunctuation,0x0384) && wcschr(titlePunctuation,0x2019));
  CHECK(StartupShowState(si) == SW_SHOWNORMAL);
  si.wShowWindow = SW_SHOWMAXIMIZED;
  CHECK(StartupShowState(si) == SW_SHOWNORMAL); // Value irrelevant without flag.
  si.dwFlags = STARTF_USESHOWWINDOW;
  CHECK(StartupShowState(si) == SW_SHOWMAXIMIZED);
  si.wShowWindow = SW_HIDE;
  CHECK(StartupShowState(si) == SW_HIDE);
  si.wShowWindow = SW_SHOWMINIMIZED;
  CHECK(StartupShowState(si) == SW_SHOWMINIMIZED);
  puts("MRU, UTF-8 source and startup show-state contracts passed.");
  return 0;
}
