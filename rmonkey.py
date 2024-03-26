# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-03-19 19:36:47
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Monkey patch methods.
"""


from __future__ import annotations


__all__ = (
    "monkey_patch_sqlalchemy_result_more_fetch",
    "monkey_patch_sqlalchemy_row_index_field",
    "monkey_patch_pprint_modify_width_judgment"
)


def monkey_patch_sqlalchemy_result_more_fetch():
    """
    Monkey patch of package `sqlalchemy`, add more fetch methods to `CursorResult` object.

    Returns
    -------
    Result object.
    """


    from typing import Optional
    from sqlalchemy.engine.cursor import CursorResult
    from pandas import DataFrame, NA, concat

    from .rstdout import echo
    from .rtable import (
        fetch_table as rtable_fetch_table,
        fetch_dict as rtable_fetch_dict,
        fetch_list as rtable_fetch_list,
        fetch_df as rtable_fetch_df,
        fetch_json as rtable_fetch_json,
        fetch_text as rtable_fetch_text,
        fetch_sql as rtable_fetch_sql,
        fetch_html as rtable_fetch_html,
        fetch_csv as rtable_fetch_csv,
        fetch_excel as rtable_fetch_excel
    )
    from .rtime import time_to


    # Fetch result as table in "List[Dict]" format.
    CursorResult.fetch_table = rtable_fetch_table

    # Fetch result as dictionary.
    CursorResult.fetch_dict = rtable_fetch_dict

    # Fetch result as list.
    CursorResult.fetch_list = rtable_fetch_list

    # Fetch result as DataFrame object.
    CursorResult.fetch_df = rtable_fetch_df

    # Fetch result as JSON string.
    CursorResult.fetch_json = rtable_fetch_json

    # Fetch result as text.
    CursorResult.fetch_text = rtable_fetch_text

    # Fetch result as SQL string.
    CursorResult.fetch_sql = rtable_fetch_sql

    # Fetch result as HTML string.
    CursorResult.fetch_html = rtable_fetch_html

    # Fetch result as save csv format file.
    CursorResult.fetch_csv = rtable_fetch_csv

    # Fetch result as save excel file.
    CursorResult.fetch_excel = rtable_fetch_excel


    # Print result.
    def method_show(self: RResult, limit: Optional[int] = None) -> None:
        """
        Print result.

        Parameters
        ----------
        limit : Limit row.
            - `>0` : Limit first few row.
            - `<0` : Limit last few row.
        """

        # Handle parameter.
        if limit is None:
            limit = 0

        # Convert.
        df: DataFrame = self.fetch_df()
        df = df.applymap(time_to, raising=False)
        df = df.astype(str)
        df.replace(["NaT", "<NA>"], "None", inplace=True)
        row_len, column_len = df.shape

        # Create omit row.
        omit_row = (("...",) * column_len,)
        omit_row = DataFrame(
            omit_row,
            columns=df.columns
        )

        # Limit.
        if (
            limit > 0
            and limit < row_len
        ):
            df = df.head(limit)
            omit_row.index = (row_len - 1,)
            df = concat((df, omit_row))
        elif (
            limit < 0
            and -limit < row_len
        ):
            df = df.tail(-limit)
            omit_row.index = (0,)
            df = concat((omit_row, df))

        # Print.
        echo(df, title="Result")


    CursorResult.show = method_show


    # Whether is exist.
    @property
    def method_exist(self: RResult) -> bool:
        """
        Judge whether is exist row.

        Returns
        -------
        Judge result.
        """

        # Judge.
        judge = self.rowcount != 0

        return judge


    CursorResult.exist = method_exist


    # Whether is empty.
    @property
    def method_empty(self: RResult) -> bool:
        """
        Judge whether is empty row.

        Returns
        -------
        Judge result.
        """

        # Judge.
        judge = self.rowcount == 0

        return judge


    CursorResult.empty = method_empty


    # Update annotations.
    class RResult(CursorResult):
        """
        Update based on `CursorResult` object, for annotation return value.
        """

        # Inherit document.
        __doc__ = CursorResult.__doc__

        # Add method.
        fetch_table = rtable_fetch_table
        fetch_dict = rtable_fetch_dict
        fetch_list = rtable_fetch_list
        fetch_df = rtable_fetch_df
        fetch_json = rtable_fetch_json
        fetch_text = rtable_fetch_text
        fetch_sql = rtable_fetch_sql
        fetch_html = rtable_fetch_html
        fetch_csv = rtable_fetch_csv
        fetch_excel = rtable_fetch_excel
        show = method_show
        exist = method_exist
        empty = method_empty


    return RResult


def monkey_patch_sqlalchemy_row_index_field():
    """
    Monkey patch of package `sqlalchemy`, add index by field method to `Row` object.
    """


    from typing import Any, Tuple, Union, overload
    from sqlalchemy.engine.row import Row


    # Define.
    @overload
    def __getitem__(self, index: Union[str, int]) -> Any: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple: ...

    def __getitem__(self, index: Union[str, int, slice]) -> Union[Any, Tuple]:
        """
        Index row value.

        Parameters
        ----------
        index : Field name or subscript or slice.

        Returns
        -------
        Index result.
        """

        # Index.
        if index.__class__ == str:
            value = self._mapping[index]
        else:
            value = self._data[index]

        return value


    # Add.
    Row.__getitem__ = __getitem__


def monkey_patch_pprint_modify_width_judgment() -> None:
    """
    Monkey patch of package `pprint`, modify the chinese width judgment.
    """


    from pprint import PrettyPrinter, _recursion


    # New method.
    def _format(_self, obj, stream, indent, allowance, context, level):


        from .rtext import get_width


        objid = id(obj)
        if objid in context:
            stream.write(_recursion(obj))
            _self._recursive = True
            _self._readable = False
            return
        rep = _self._repr(obj, context, level)
        max_width = _self._width - indent - allowance
        width = get_width(rep)
        if width > max_width:
            p = _self._dispatch.get(type(obj).__repr__, None)
            if p is not None:
                context[objid] = 1
                p(_self, obj, stream, indent, allowance, context, level + 1)
                del context[objid]
                return
            elif isinstance(obj, dict):
                context[objid] = 1
                _self._pprint_dict(obj, stream, indent, allowance,
                                context, level + 1)
                del context[objid]
                return
        stream.write(rep)


    # Modify.
    PrettyPrinter._format = _format


def monkey_path_pil_image_get_bytes():
    """
    Monkey patch of package `PIL`, add get bytes method to `Image` object.

    Returns
    -------
    Image object.
    """


    from PIL.Image import Image
    from io import BytesIO


    # Define.
    def method_get_bytes(self: Image) -> bytes:
        """
        Get image bytes data.

        Returns
        -------
        Image bytes data.
        """

        # Extract.
        bytes_io = BytesIO()
        self.save(bytes_io, "JPEG")
        image_bytes = bytes_io.getvalue()

        return image_bytes


    # Add.
    Image.get_bytes = method_get_bytes


    # Update annotations.
    class RImage(Image):
        """
        Update based on `Image` object, for annotation return value.
        """

        # Inherit document.
        __doc__ = Image.__doc__

        # Add method.
        get_bytes = method_get_bytes


    return RImage